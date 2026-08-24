import { Module } from '@nestjs/common';
import { DatabaseModule } from '../datasources/database.module';

import { TiendaController } from './controllers/tienda.controller';
import { TiendaRepository } from './repositories/tienda.repository';
import { repositoryProviders } from './repositories/repository.providers';
import { TiendaService } from './services/tienda.service';

@Module({
  imports: [DatabaseModule],
  controllers: [TiendaController],
  providers: [
    ...repositoryProviders,
    TiendaRepository,
    TiendaService,
  ],
  exports: [TiendaService],
})
export class IdentificacionModule {}